from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import router

app = FastAPI()
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ← "all_origin" → "allow_origins"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



# Header -> info. oif user
# Payload -> Meta deta of user -> "H5256"
# {
    # user_id : ;
    # email: ;
    # Role: "Adain";
    # enp: Time of token enpire
    # iat : issued at what time
# }

# Signature;
#         -> Hashed Combination of header and payload
# Hash (Header + Payload + Secret key)

# pip freeze > requirements.txt
