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
    private int seriesInStudy;

    @CsvBindByPosition(position = 5)
    private String iStart;

    @CsvBindByPosition(position = 6)
    private String iEnd;

    @CsvBindByPosition(position = 7)
    private String studyDescription;

    @CsvBindByPosition(position = 8)
    private String modality;

    @Override
    public String getScanner() {
        return scanner;
    }

    @Override
    public String getDetails() {
        return studyDescription;
    }

    @Override
    public void produceFinal(int index, String date) {
        ScannerSingleton ss = ScannerSingleton.getInstance(date);
        ss.addToScannerHashmap(this.scanner, this.patientID, this.iStart, this.iEnd, this.iDuration,
                this.studyDescription, this.modality, this.seriesInStudy);
    }
}