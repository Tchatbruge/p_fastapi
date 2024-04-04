from uuid import uuid4


database = {
    "books": [
        {
            "ISBN": str(uuid4()),
            "author": "Jason Jefferson",
            "editor": "Defro record!",
            "book_name": "paradis naruto",
        },
        {
            "ISBN": str(uuid4()),
            "author": "Bruge tcha",
            "editor": "Defro record !",
            "book_name": "fulmetal",
        },
        {
            "ISBN": str(uuid4()),
            "author": "Chainsoman",
            "editor": "Bad boys record !",
            "book_name": "One piece",
        },
    ],
"users": [
        {
            "id": str(uuid4()),
            "username": "jason",
            "email":"jason@gmail.com",
            "password": "123456",
        },
        {
            "id": str(uuid4()),
            "username": "jefferson",
            "email": "jefferson@gmail.com",
            "password": "aominerjefferson",
        },
    ]
}