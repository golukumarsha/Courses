from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from routers import router
 
app = FastAPI()
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
 
app.include_router(router)
 
# ✅ Frontend - single HTML file (CSS + JS sab inline hai)
@app.get("/ui", include_in_schema=False)
def serve_frontend():
    return FileResponse("index.html")

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
