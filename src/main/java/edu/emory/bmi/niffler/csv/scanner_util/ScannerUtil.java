package edu.emory.bmi.niffler.csv.scanner_util;

import edu.emory.bmi.niffler.csv.core.AbstractCsvBean;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class ScannerUtil {
    private static Logger logger = LogManager.getLogger(ScannerUtil.class.getName());

    private static List<Scanner> scannerList = new ArrayList<>();

    public static void updateScannerList(Scanner scanner) {
        scannerList.add(scanner);
    }

    public static void getFinalCsvString(
            List<AbstractCsvBean> beans, String filename, Map<String, String> scannersSubsetMap) {
        for (AbstractCsvBean bean: beans) {
            bean.produceFinal();
        }
        ScannerSingleton ss = ScannerSingleton.getInstance();
        ss.produceFinalCSV(filename, scannersSubsetMap);
    }

    public static double getDiffInMins(String start, String end) {
        String startTime = String.valueOf(Double.parseDouble(start) + 240000);
        String endTime = String.valueOf(Double.parseDouble(end) + 240000);
        double durationInMins;

        try {
            durationInMins = (Double.parseDouble(endTime.substring(0,2)) -
                    Double.parseDouble(startTime.substring(0,2))) * 60.0 +
                    (Double.parseDouble(endTime.substring(2,4)) -
                            Double.parseDouble(startTime.substring(2,4))) +
                    (Double.parseDouble(endTime.substring(4,6)) -
                            Double.parseDouble(startTime.substring(4,6))) / 60.0  ;

        } catch (Exception e) {
            logger.error("Calculating duration failed");
            durationInMins = 99999;
        }
        return durationInMins;
    }

}
