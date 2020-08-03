package edu.emory.bmi.niffler.csv.scanner_util;

import edu.emory.bmi.niffler.util.NifflerConstants;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class ScannerSingleton {
    private static Map<String, ScannerSingleton> singleton = new HashMap<>();
    private static Logger logger = LogManager.getLogger(ScannerSingleton.class.getName());
    private static String outputFile = NifflerConstants.FINAL_DIRECTORY + "/" + NifflerConstants.FINAL_FILE;
    private static boolean isFirstIter = true;
    private static boolean isFirstEntry = true;

    private Map<String, Scanner> scannerHashMap;

    private ScannerSingleton() {
        scannerHashMap = new HashMap<>();
    }

    public static ScannerSingleton getInstance(String ssName) {
        if (singleton.get(ssName) == null) {
            ScannerSingleton ss = new ScannerSingleton();
            singleton.put(ssName, ss);
        }
        return singleton.get(ssName);
    }

    public void addToScannerHashmap(String scannerID, String patientID, String iStart, String iEnd, double duration, String studyDescription) {
        if (scannerHashMap.containsKey(scannerID)) {
            Scanner scannerObj = scannerHashMap.get(scannerID);
            scannerObj.addToPatientHashmap(patientID, iStart, iEnd, duration, studyDescription);
            scannerHashMap.replace(scannerID, scannerObj);
        } else {
            Scanner scannerObj = new Scanner(scannerID, patientID, iStart, iEnd, duration, studyDescription);
            scannerHashMap.put(scannerID, scannerObj);
        }
    }

    public void produceFinalCSV(int index, String date, Map<String, String> scannersSubsetMap) {
        traverseScannerHashMap(index, date, scannersSubsetMap);
    }


    public void traverseScannerHashMap(int index, String date, Map<String, String> scannersSubsetMap) {
        StringBuilder out = new StringBuilder();
        String str = "";
        for (Scanner scanner: scannerHashMap.values()) {
            if (scannersSubsetMap.containsKey(scanner.getScannerID())) {
                out.append(scanner.traversePatientHashMap(index, date));
            }
        }

        String title = "Date #, Date YYYYMMDD, ScannerID, Scanner Utilization %, Patients per scanner, " +
                "Exams per scanner \n , , , , , , PatientID, StartTime, EndTime, Duration (Minutes), " +
                "Number of Studies In the Exam, Study Description \n";
        if (isFirstEntry) {
            str = title + out;
            isFirstEntry = false;
        } else {
            str = out.toString();
        }
        writeToFile(str);
    }

    public void writeToFile(String str) {
        try {
            BufferedWriter writer;
            if (isFirstIter) {
                 writer = new BufferedWriter(new FileWriter(outputFile));
                isFirstIter = false;
            } else {
                //Set to true is to append
                writer = new BufferedWriter(new FileWriter(outputFile, true));
            }
            writer.write(str);
            writer.close();
            logger.info("Written the output to the final csv file.");
        } catch (IOException e) {
            logger.error("IOException occurred while writing the final csv. " + e);
        }
    }
}
