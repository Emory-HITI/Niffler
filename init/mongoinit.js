conn = new Mongo();
db = conn.getDB("admin");
db.createUser(
   {
     user: "researchpacsroot",
     pwd: passwordPrompt(),  // Or  "<cleartext password>"
     roles: [{role:"root", db:"admin"}]
   }
);

conn.close();
quit();
