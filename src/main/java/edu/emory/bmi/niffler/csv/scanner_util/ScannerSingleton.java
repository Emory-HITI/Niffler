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
    private static ScannerSingleton singleton = null;
    private static Logger logger = LogManager.getLogger(ScannerSingleton.class.getName());

    private Map<String, Scanner> scannerHashMap;
    private String outputFile;

    private ScannerSingleton() {
        scannerHashMap = new HashMap<>();
    }

    public static ScannerSingleton getInstance() {
        if (singleton == null)
            singleton = new ScannerSingleton();
        return singleton;
    }

    public void addToScannerHashmap(String scannerID, String patientID, String iStart, String iEnd, double duration) {
        if (scannerHashMap.containsKey(scannerID)) {
            Scanner scannerObj = scannerHashMap.get(scannerID);
            scannerObj.addToPatientHashmap(patientID, iStart, iEnd, duration);
            scannerHashMap.replace(scannerID, scannerObj);
        } else {
            Scanner scannerObj = new Scanner(scannerID, patientID, iStart, iEnd, duration);
            scannerHashMap.put(scannerID, scannerObj);
        }
    }

    public void produceFinalCSV(String filename, Map<String, String> scannersSubsetMap) {
        outputFile = NifflerConstants.FINAL_DIRECTORY + "/final_" + filename ;
        traverseScannerHashMap(scannersSubsetMap);
    }


    public void traverseScannerHashMap(Map<String, String> scannersSubsetMap) {
        StringBuilder out = new StringBuilder();
        for (Scanner scanner: scannerHashMap.values()) {
            if (scannersSubsetMap.containsKey(scanner.getScannerID())) {
                out.append(scanner.traversePatientHashMap());
            }
        }
        String str = "ScannerID, Scanner Utilization % \n , , PatientID, StartTime, EndTime, Duration (Minutes), Studies Merged? \n" + out;
        writeToFile(str);
    }

    public void writeToFile(String str) {
        try {
            BufferedWriter writer = new BufferedWriter(new FileWriter(outputFile));
            writer.write(str);
            writer.close();
            logger.info("Written the output to the final csv file.");
        } catch (IOException e) {
            logger.error("IOException occurred while writing the final csv. " + e);
        }
    }
}
