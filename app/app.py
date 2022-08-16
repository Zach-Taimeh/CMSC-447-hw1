from flask import Flask, render_template, request
from pymongo import MongoClient


try:
    cluster = MongoClient("mongodb+srv://ztaimeh:1iV38GiwXetjRkDz@cluster0.oxyzl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = cluster["people_db"]
    col = db["people"]
except Exception as e:
    print(e)

app = Flask(__name__)

class entry():
    def __init__(self, name, points, id):
        self.name = name
        self.points = points
        self._id = id

# read all records in db and display
@app.route("/readall")
def readall():
    records = []
    data = col.find()
    for record in data:
        usr = entry(name = record['name'], points = record['points'], id = record['_id'])
        records.append(usr)
    if records:
        return render_template("viewall.html", values=records, content="View Records", result= "Found Entries:", title="View Records")
    else:
        return render_template("viewall.html",  content="View Records", result = "No Entries Found", title="View Records")

# read requested records and display, names are case sensitive and comma delimited.
@app.route("/read", methods=["POST", "GET"])
def read():
    if request.method == "POST":
        records = []
        not_found_records = []
        usr = None
        ids = request.form["id"]
        ids = ids.replace(" ", "")
        ids = ids.split(",")
        names = request.form["nm"]
        names = names.split(",")

        ids = [string for string in ids if string!= ""]
        names = [name.strip() for name in names]
        names = [string for string in names if string!= ""]
        print(f"search ids: {ids}")
        print(f"search names: {names}")

        for id in ids:
            record = col.find_one({"_id":int(id)})
            if record is not None:
                usr = entry(name = record['name'], points = record['points'], id = record['_id'])
                records.append(usr)
            else:
                print(f"ID: {id} not found")
                not_found_records.append(id)

        for name in names:
            record = col.find_one({"name":str(name)})
            if record is not None:
                usr = entry(name = record['name'], points = record['points'], id = record['_id'])
                records.append(usr)
            else:
                print(f"Name: {name} not found")
                not_found_records.append(f"Name: {name}")

        if records:
            if not_found_records:
                return render_template("view.html", values=records, content="View Records", result= "Found Entries:", not_found = "Entries Not Found:",
            not_found_entries=not_found_records, title="View Records")
            return render_template("view.html", values=records, content="View Records", result= "Found Entries:", title="View Records")
        else:
            return render_template("view.html",  content="View Records", result = "No Entries Found", title="View Records")

    else:
        return render_template("view.html", title="View Records", content="View Records")

#update record name/points using id as key
@app.route("/update", methods=["POST", "GET"])
def update():
    if request.method == "POST":
        name = request.form["nm"]
        id = request.form["id"]
        points = request.form["pts"]
        data = {'_id':int(id), 'name':str(name), 'points':int(points)}
        result = col.update_one({"_id":int(id)}, {"$set": data}, upsert=False)
        if result.matched_count == 0:
            return render_template("update.html", title="Update Records", content="Update failed; record not found.")
        else:
            return render_template("update.html", title="Update Records", content=f"Updated Entry {id}")
    else:
        return render_template("update.html", title="Update Records", content="Update Records")

#delete a record by key only
@app.route("/delete", methods=["POST", "GET"])
def delete():
    if request.method == "POST":
        records = []
        not_found_records = []
        usr = None
        ids = request.form["id"]
        ids = ids.replace(" ", "")
        ids = ids.split(",")
        ids = [string for string in ids if string!= ""]

        for id in ids:
            record = col.find_one_and_delete({"_id":int(id)})
            if record is not None:
                usr = entry(name = record['name'], points = record['points'], id = record['_id'])
                print(record['name'])
                print(record['points'])
                print(record['_id'])
                records.append(usr)
            else:
                print(f"ID: {id} not found")
                not_found_records.append(id)

        if records:
            if not_found_records:
                return render_template("delete.html", values=records, content="Delete Records", result= "Found Entries:", not_found = "Entries Not Found:",
            not_found_entries=not_found_records, title="Delete Records")
            return render_template("delete.html", values=records, content="View Records", result= f"Entry {record['_id']} : {record['name']} Deleted", title="Delete Records")
        else:
            return render_template("delete.html",  content="Delete Records", result = "No Entries Found", title="Delete Records")

    else:
        return render_template("delete.html", title="Delete Records", content="Delete Records")

#ID is automatically assigned when creating new entries to avoid key errors.
@app.route("/", methods=["POST", "GET"])
@app.route("/create", methods=["POST", "GET"])
def send():
    if request.method == "POST":
        name = request.form["nm"]
        points = request.form["pts"]
        lastrecord = col.find_one({"$query": {}, "$orderby": {"$natural" : -1}})
        if name and points:
            data = {'_id':int(lastrecord["_id"]+1), 'name':str(name), 'points':int(points)}
            col.insert_one(data)
            return render_template("index.html", value=name, title="Create Entry", entry=f"Entry for {name} created with id: {lastrecord['_id']+1}")
        else:
            return render_template("index.html", content="Create an entry", title="Create Entry", error="Please enter a name and points!")
    else:
        return render_template("index.html", content="Create an entry", title="Create Entry")


if __name__ == "__main__":
    app.run(debug=True)