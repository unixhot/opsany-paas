#!/usr/bin/env python3

import sys
import bcrypt

password = sys.argv[1]
hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
print(hashed_password.decode())
