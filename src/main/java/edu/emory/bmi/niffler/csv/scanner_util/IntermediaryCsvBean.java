package edu.emory.bmi.niffler.csv.scanner_util;

import com.opencsv.bean.CsvBindByPosition;
import edu.emory.bmi.niffler.csv.core.AbstractCsvBean;


public class IntermediaryCsvBean extends AbstractCsvBean {

    @CsvBindByPosition(position = 0)
    private String scanner;

    @CsvBindByPosition(position = 1)
    private String studyID;

    @CsvBindByPosition(position = 2)
    private String patientID;

    @CsvBindByPosition(position = 3)
    private double iDuration;

    @CsvBindByPosition(position = 4)
    private String seriesInStudy;

    @CsvBindByPosition(position = 5)
    private String iStart;

    @CsvBindByPosition(position = 6)
    private String iEnd;

    @CsvBindByPosition(position = 7)
    private String studyDescription;

    @Override
    public String getScanner() {
        return scanner;
    }

    @Override
    public String getDetails() {
        return seriesInStudy;
    }

    @Override
    public void produceFinal(String fileName) {
        ScannerSingleton ss = ScannerSingleton.getInstance(fileName);
        ss.addToScannerHashmap(this.scanner, this.patientID, this.iStart, this.iEnd, this.iDuration, this.studyDescription);
    }
}