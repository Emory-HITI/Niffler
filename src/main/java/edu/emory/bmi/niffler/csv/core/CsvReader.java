package edu.emory.bmi.niffler.csv.core;

import com.opencsv.bean.ColumnPositionMappingStrategy;
import com.opencsv.bean.CsvToBean;
import com.opencsv.bean.CsvToBeanBuilder;
import com.opencsv.exceptions.CsvValidationException;
import edu.emory.bmi.niffler.csv.scanner_util.FilterCsvBean;
import edu.emory.bmi.niffler.csv.scanner_util.IntermediaryCsvBean;
import edu.emory.bmi.niffler.util.NifflerConstants;
import edu.emory.bmi.niffler.csv.scanner_util.ScannerUtil;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.File;
import java.io.IOException;
import java.io.Reader;
import java.net.URISyntaxException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Read CSV files
 */
public class CsvReader {
    private static Logger logger = LogManager.getLogger(CsvReader.class.getName());

    /**
     * Reads the files in the intermediary csv folder
     * @throws IOException if the execution failed
     */
    public static void readIntermediaryCSVFolder() throws IOException {
        File folder = new File(NifflerConstants.INTERMEDIARY_DIRECTORY);
        File subset = new File(NifflerConstants.SUBSET_SCANNERS);

        File[] listOfFiles = folder.listFiles();
        try {
            String subsetStr = subset.toString();
            Path subsetPath = Paths.get(subsetStr);
            List<AbstractCsvBean> subsetout = convertToBean(subsetPath, FilterCsvBean.class);

            Map<String, String> scannersSubsetMap = new HashMap<>();

            for (AbstractCsvBean fbean: subsetout) {
                scannersSubsetMap.put(fbean.getScanner(), fbean.getDetails());
            }

            for (File file: listOfFiles) {
                String fileStr = file.toString();
                Path path = Paths.get(fileStr);
                List<AbstractCsvBean> out = convertToBean(path, IntermediaryCsvBean.class);
                ScannerUtil.getFinalCsvString(out, file.getName(), scannersSubsetMap);
            }

            } catch (URISyntaxException e) {
                logger.error("URI Syntax Exception Occurred: " + e);
            } catch (CsvValidationException e) {
                logger.error("CSV Validation Exception Occurred: " + e);
            } catch (Exception e) {
                logger.error("Exception Occurred: " + e);
            }

    }

    /**
     * Convert the text into a bean
     * @param path the path to read the csv file
     * @param clazz the bean class
     * @return the list of csv beans
     * @throws Exception if bean reading failed
     */
    public static List<AbstractCsvBean> convertToBean(Path path, Class clazz) throws Exception {
        CsvTransfer csvTransfer = new CsvTransfer();
        ColumnPositionMappingStrategy ms = new ColumnPositionMappingStrategy();
        ms.setType(clazz);

        Reader reader = Files.newBufferedReader(path);

        CsvToBean cb = new CsvToBeanBuilder(reader)
                .withType(clazz)
                .withMappingStrategy(ms)
                .build();

        csvTransfer.setCsvList(cb.parse());
        reader.close();
        return csvTransfer.getCsvList();
    }
}
