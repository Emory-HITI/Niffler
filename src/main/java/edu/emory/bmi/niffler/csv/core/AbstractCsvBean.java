package edu.emory.bmi.niffler.csv.core;

public abstract class AbstractCsvBean {

    public abstract void produceFinal(int index, String fileName);

    public abstract String getScanner();

    public abstract String getDetails();

    }
