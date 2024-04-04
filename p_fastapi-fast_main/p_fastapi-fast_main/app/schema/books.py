from pydantic import BaseModel, Field 

class Books(BaseModel):
    ISBN: str
    author: str = Field(min_lenght=2 , max_length=30)
    editor: str = Field(min_length=2 , max_length=30)
    book_name: str = Field(min_length= 2 , max_length = 30)