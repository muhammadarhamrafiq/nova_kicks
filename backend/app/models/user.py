from beanie import Document, Insert, Replace, before_event
from pwdlib import PasswordHash


pwd_context = PasswordHash.recommended()


class User(Document):
    username: str
    password: str

    @before_event(Insert, Replace)
    def hash_password(self) -> None:
        # check if the password is already hashed
        if not self.password.startswith('$argon2'):
            self.password = pwd_context.hash(password=self.password)

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(password=plain_password, hash=self.password)

    class Settings:
        name = 'users'
