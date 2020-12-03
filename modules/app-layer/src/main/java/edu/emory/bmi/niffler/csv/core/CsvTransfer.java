package edu.emory.bmi.niffler.csv.core;

import java.util.ArrayList;
import java.util.List;

public class CsvTransfer {

    private List<String[]> csvStringList;

    private List<AbstractCsvBean> csvList;

    public CsvTransfer() {}

    public List<String[]> getCsvStringList() {
        if (csvStringList != null) return csvStringList;
        return new ArrayList<String[]>();
    }

    public void addLine(String[] line) {
        if (this.csvList == null) this.csvStringList = new ArrayList<>();
        this.csvStringList.add(line);
    }

    public void setCsvStringList(List<String[]> csvStringList) {
        this.csvStringList = csvStringList;
    }

    public void setCsvList(List<AbstractCsvBean> csvList) {
        this.csvList = csvList;
    }

    public List<AbstractCsvBean> getCsvList() {
        if (csvList != null) return csvList;
        return new ArrayList<>();
    }
}