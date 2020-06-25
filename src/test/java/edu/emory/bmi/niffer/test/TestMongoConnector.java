package edu.emory.bmi.niffer.test;

import com.mongodb.client.MongoDatabase;
import com.mongodb.client.MongoIterable;
import edu.emory.bmi.niffler.mongo.MongoConnector;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.junit.Test;

import static org.junit.Assert.fail;

/**
 * Test the connection to Mongo data source
 */
public class TestMongoConnector {
	private static Logger logger = LogManager.getLogger(TestMongoConnector.class.getName());

	/**
	 *  Method: GetCollectionValues
	 *  Description: Returns  set of all collection values
	 */
	@Test
	public void testConnect() {

		MongoConnector mongoConnector = new MongoConnector();
			try {
			MongoDatabase database = mongoConnector.connect("localhost", 27017, "mongo",
					"mongo", "admin", "testdb");
			MongoIterable<String> collections = database.listCollectionNames();

			for (String col : collections) {
				logger.info(col);
			}
		} catch (Exception e) {
			fail(e.getMessage()); // request failed
		}
	}
}
