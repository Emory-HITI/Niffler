package edu.emory.bmi.niffler.util;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

/**
 * Execute the core workflow
 */
public class NifflerExecutor {
	private static Logger logger = LogManager.getLogger(NifflerExecutor.class.getName());

	public static void execute() {
		long startTime = System.currentTimeMillis();


		long endTime = System.currentTimeMillis();
		long duration = (startTime - endTime);

		logger.info("The execution took: " + duration / 1000.0 + " seconds.");

	}
}
