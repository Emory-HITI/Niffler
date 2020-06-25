package edu.emory.bmi.niffler.mongo;

import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoDatabase;
import edu.emory.bmi.niffler.util.NifflerConstants;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class MongoConnector {

	private static Logger logger = LogManager.getLogger(MongoConnector.class.getName());

	/**
	 * Connect to the Mongo database
	 * @param connectionURI the connection URI
	 * @param db the database to connect to
	 * @return the connected database object
	 */
	public MongoDatabase connect(String connectionURI, String db) {
		MongoClient mongoClient = MongoClients.create(connectionURI);
		MongoDatabase database = mongoClient.getDatabase(db);
		return database;
	}

	/**
	 * When Mongod started with --auth secured option
	 * @param host the host of mongodb
	 * @param port the port of mongodb
	 * @param db the database to connect to
	 * @param username the user name to authenticate with
	 * @param password the password to authenticate with
	 * @param authdb the database to authenticate against
	 * @return the connected database object
	 */
	public MongoDatabase connect(String host, int port, String username, String password, String authdb, String db) {
		String connectionURI = buildConnectionURI(host, port, username, password, authdb);
		MongoClient mongoClient = MongoClients.create(connectionURI);

		MongoDatabase database = mongoClient.getDatabase(db);
		return database;
	}

	/**
	 * mongodb://user1:pwd1@host1/?authSource=db1
	 * @param host the host name: default: localhost
	 * @param port the port : default: 27017
	 * @param username, the user name
	 * @param password, the password
	 * @param authdb, the authdb
	 * @return the connectionURI string
	 */
	private String buildConnectionURI(String host, int port, String username, String password, String authdb) {

		String connectionURI = NifflerConstants.MONGO_CONNECTION_STRING_PREFIX + username + ":" + password + "@" +
				host + ":" + port + "/?" + NifflerConstants.MONGO_AUTH_SOURCE_PREFIX + "=" + authdb;
		return connectionURI;
	}
}
