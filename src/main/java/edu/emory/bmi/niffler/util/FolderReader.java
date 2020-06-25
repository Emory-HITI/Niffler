package edu.emory.bmi.niffler.util;

/**
 * Sample code that finds files that match the specified glob pattern.
 * For more information on what constitutes a glob pattern, see
 * https://docs.oracle.com/javase/tutorial/essential/io/fileOps.html#glob
 * <p>
 * The file or directories that match the pattern are printed to
 * standard out.  The number of matches is also printed.
 * <p>
 * When executing this application, you must put the glob pattern
 * in quotes, so the shell will not expand any wild cards:
 * java Find . -name "*.java"
 */

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.*;
import java.nio.file.*;
import java.nio.file.attribute.*;
import java.util.stream.Stream;

import static java.nio.file.FileVisitResult.*;


public class FolderReader extends SimpleFileVisitor<Path> {

	private final PathMatcher matcher;
	private static Logger logger = LogManager.getLogger(FolderReader.class.getName());


	public FolderReader(String pattern) {
		matcher = FileSystems.getDefault().getPathMatcher("glob:" + pattern);
	}

	// Compares the glob pattern against
	// the file or directory name.
	public void find(Path file) {
		Path name = file.getFileName();
		if (name != null && matcher.matches(name)) {
			readFile(file.toString());
		}
	}

	public static void readFile(String file) {
		try (Stream<String> stream = Files.lines(Paths.get(file))) {
			stream.forEach(System.out::println);
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	// Invoke the pattern matching
	// method on each file.
	@Override
	public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
		find(file);
		return CONTINUE;
	}

	// Invoke the pattern matching
	// method on each directory.
	@Override
	public FileVisitResult preVisitDirectory(Path dir, BasicFileAttributes attrs) {
		find(dir);
		return CONTINUE;
	}

	@Override
	public FileVisitResult visitFileFailed(Path file, IOException exc) {
		logger.error(exc);
		return CONTINUE;
	}


	public static void usage() {
		logger.error("java Find <path>" +
				" -name \"<glob_pattern>\"");
		System.exit(-1);
	}

	/**
	 * Reads the files in the feature folder
	 * @throws IOException if the execution failed
	 */
	public static void readFeatureFolder() throws IOException {
		readFolder(NifflerConstants.FEATURES_DIRECTORY, NifflerConstants.TXT_FILE_PATTERN);
	}

	/**
	 * Reads the files in any given folder
	 * @param folder, the folder to read
	 * @param fileExtension, the extension of the files to read.
	 * @throws IOException if the execution failed
	 */
	public static void readFolder(String folder, String fileExtension) throws IOException {
		Path startingDir = Paths.get(folder);

		FolderReader folderReader = new FolderReader(fileExtension);

		Files.walkFileTree(startingDir, folderReader);
	}
}