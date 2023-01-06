import base64
from typing import Union
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

import motor.motor_asyncio
from bson.objectid import ObjectId

import pyTigerGraph as tg
from pydantic import ConfigError

#mongo connection
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
database = client.photo_library
photo_collection = database.get_collection("photos")

#Add a new photo to mongodb
async def add_photo_to_MongoDB(photo_data:dict):
    try:
        entry = await photo_collection.insert_one(photo_data)
        return str(entry.inserted_id)
    except:
        return False

#Get a a specific photo via its ID
async def retrieve_photo_from_MongoDB(id:str):
    try:
        entry = await photo_collection.find_one({"_id":ObjectId(id)})
        if entry:
            return entry
        else:
            return False
    except:
        return False

###############################################
#TigerGraph
mySecret = "mySecret"
authToken="myToken"

# conn = tg.TigerGraphConnection(host=Domain, graphname=Graph, gsqlSecret=Secret)

# authToken = conn.getToken(Secret)
# authToken = authToken[0]

conn = tg.TigerGraphConnection(
    host="https://my-graph.i.tgcloud.io",
    graphname="photos",
    gsqlSecret=mySecret,
    apiToken=authToken
)
# print(conn.getVertexCount("*"))
# newAuthToken = conn.getToken(mySecret)
# newAuthToken = newAuthToken[0]
# print(newAuthToken)

#query to add photo data to TigerGraph
async def add_photo_query(id:str, tags:list):
    try:
        conn.upsertVertex("Photo", id, {"id":id})
        hasTagList = []
        for t in tags:
            conn.upsertVertex("Tag", t, {"id":t})
            hasTagList.append((id, t))
        conn.upsertEdges("Photo", "PHOTO_HAS_TAG", "Tag", hasTagList)
        return True
    except:
        return False

#query to get all photo ids and tags from the graph
async def retrieve_all_photos_query():
    try:
        data = conn.runInstalledQuery("FetchAllPhotoData", {})
        return data[0]["photos"]
    except:
        return False

app = FastAPI()

# Allow for api calls from external sources
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello":"World"}

#API Endpoints
# upload a photo to mongo and photo id and tag to TigerGraph
@app.post("/uploadPhoto/")
async def upload_photo(file:UploadFile, tags:list):
    tags = tags[0].split(',')
    contents = await file.read()
    data = {"photo":contents}
    photoID = await add_photo_to_MongoDB(data)
    added = await add_photo_query(photoID, tags)
    if added:
        return {"code":200, "message":"Photo uploaded"}
    else:
        return {"code":401, "message": "Photo upload failed"}

#given photo id retrieve photo from mongo
@app.put("/retrievePhoto/{id}")
async def retrievePhoto(id:str):
    data = await retrieve_photo_from_MongoDB(id)
    if not data:
        return {"code":401, "message":"Failed to get photo"}
    contents = data["photo"]
    contents=base64.b64encode(contents)
    return Response(content=contents, media_type="image/png")

#retrieve all photo id and tag data from TigerGraph
@app.put("/retrieveAllPhotoInfo/")
async def retrieve_all_photo_info():
    data = await retrieve_all_photos_query()
    if not data:
        return {"code":401, "message":"Failed to retrieve photo"}
    else:
        return {"code":200, "data":data, "message":"Photo data fetched"}