from pymongo.mongo_client import MongoClient

# Corrected MongoDB URI — removed angle brackets from password
uri = "mongodb+srv://Asthavashisth:Av13062004@cluster0.4v0ifdt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
