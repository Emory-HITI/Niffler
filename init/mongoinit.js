conn = new Mongo();
use admin;
db.createUser(
   {
     user: "researchpacsroot",
     pwd: passwordPrompt(),  // Or  "<cleartext password>"
     roles: ["root"]
   }
);

conn.close();
quit();
