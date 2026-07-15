from src.auth.jwt_service import JwtService

class TestJwtService:
  def test_generate_token(self):
    token = JwtService.generate(1, 'msosa')

    assert token.__class__ == str

  def test_verify_token(self):
    token = JwtService.generate(1, 'msosa')

    token_dict = JwtService.verify(token)
    print(token_dict)

    assert token_dict['sub'] == '1'
    assert token_dict['user'] == 'msosa'
