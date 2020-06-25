package edu.emory.bmi.niffer.test;

import edu.emory.bmi.niffler.csv.core.CsvReader;
import edu.emory.bmi.niffler.util.FolderReader;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.junit.Test;

import java.io.IOException;


public class TestFolderReader {
	private static Logger logger = LogManager.getLogger(TestFolderReader.class.getName());

	@Test
	public void testReadFeatureFolder() {

		try {
			logger.info("Reading the Features Folder");
			FolderReader.readFeatureFolder();
		} catch (IOException e) {
			logger.error("Reading the features folder failed.", e);
		}
	}

	@Test
	public void testReadIntermediaryCSVFolder() {

		try {
			logger.info("Reading the CSV Folder");
			CsvReader.readIntermediaryCSVFolder();
		} catch (IOException e) {
			logger.error("Reading the CSV folder failed.", e);
		}
	}
}
