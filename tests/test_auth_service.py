import pytest
from unittest.mock import MagicMock, patch
from app.services.auth_service import AuthService, InvalidCredentialsError

class TestAuthService:
    @pytest.fixture
    def auth_service(self):
        self.db_session = MagicMock()
        return AuthService(self.db_session)

    # --- LOGOWANIE TRADYCYJNE ---

    @patch('app.services.auth_service.check_password_hash')
    def test_login_success(self, mock_check_hash, auth_service):
        """TC_LOG_01: Poprawne logowanie podróżnego przy prawidłowych danych."""
        # Znalezienie użytkownika
        mock_user = MagicMock()
        mock_user.password_hash = "hashed_pw"
        auth_service.traveler_repository.find_by_login = MagicMock(return_value=mock_user)
        
        # Poprawnego hasło
        mock_check_hash.return_value = True
        
        user, role = auth_service.login("test_user", "password123")
        
        assert role == "traveler"
        assert user == mock_user
        auth_service.traveler_repository.find_by_login.assert_called_with("test_user")

    @patch('app.services.auth_service.check_password_hash')
    def test_login_wrong_password(self, mock_check_hash, auth_service):
        """TC_LOG_02: Próba logowania z błędnym hasłem dla istniejącego użytkownika."""
        mock_user = MagicMock()
        mock_user.password_hash = "correct_hash"
        auth_service.traveler_repository.find_by_login = MagicMock(return_value=mock_user)
        
        # Błędne hasło
        mock_check_hash.return_value = False
        
        with pytest.raises(InvalidCredentialsError) as excinfo:
            auth_service.login("istniejacy_user", "bledne_haslo")
        
        assert str(excinfo.value) == "Niepoprawne dane logowania"

    def test_login_validation_empty_data(self, auth_service):
        """TC_LOG_05: Walidacja braku wymaganych danych (login/hasło)."""

        with pytest.raises(ValueError, match="Brak loginu lub hasła"):
            auth_service.login("", "haslo123")
        
        with pytest.raises(ValueError, match="Brak loginu lub hasła"):
            auth_service.login("user123", "")
        
        with pytest.raises(ValueError, match="Brak loginu lub hasła"):
            auth_service.login(None, None)

    # --- SEKCJA: INTEGRACJA MOBYWATEL ---

    def test_mobywatel_new_user(self, auth_service):
        """TC_LOG_03: Logowanie mObywatel dla nowego użytkownika (pierwszy raz)."""
        # Scenariusz 'new' powinien zwrócić tożsamość do uzupełnienia profilu
        scenario = "new"
        
        identity, user = auth_service.mobywatel_callback(scenario)
        
        assert identity is not None
        assert identity["first_name"] == "Anna"
        assert user is None  # Użytkownik nie istnieje jeszcze w bazie

    def test_mobywatel_existing_user(self, auth_service):
        """TC_LOG_04: Logowanie mObywatel dla powracającego użytkownika (kolejny raz)."""
        # Scenariusz 'existing' - system rozpoznaje użytkownika po PESEL
        scenario = "existing"
        mock_existing_user = MagicMock()
        mock_existing_user.pesel = "12345678901"
        auth_service.traveler_repository.find_by_pesel = MagicMock(return_value=mock_existing_user)
        
        identity, user = auth_service.mobywatel_callback(scenario)
        
        assert identity is None  # Nie zwraca nowej tożsamości, bo użytkownik jest znany
        assert user == mock_existing_user
        assert user.pesel == "12345678901"