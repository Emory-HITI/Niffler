package edu.emory.bmi.niffler.csv.scanner_util;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.util.Collection;
import java.util.HashMap;
import java.util.Map;

import static edu.emory.bmi.niffler.csv.scanner_util.ScannerUtil.getDiffInMins;

/**
 * Represent a single scanner
 */
public class Scanner {

    private Map<String, Patient> patientHashMap = new HashMap<>();
    private String scannerID;
    private String begin;
    private String end;
    private double totalDuration;
    private static Logger logger = LogManager.getLogger(Patient.class.getName());

    public String getScannerID() {
        return scannerID;
    }

    public double getTotalDuration() {
        return totalDuration;
    }

    public String getUtilizedPercentage() {
        double usedDuration = 0.0;
        double utilizationPercentage = 0.0;
        Collection<Patient> patients = patientHashMap.values();
        for (Patient p : patients) {
            usedDuration += p.getDurationInMins();
        }
        utilizationPercentage = (usedDuration / totalDuration) * 100;
        return utilizationPercentage + " %";
    }

    public void addToPatientHashmap(String patientID, String iStart, String iEnd, double duration, String studyDescription) {
        if (getDiffInMins(begin, iStart) < 0) {
            begin = iStart;
        }
        if (getDiffInMins(end, iEnd) > 0) {
            end = iEnd;
        }
        totalDuration = getDiffInMins(begin, end);
        addPatient(patientID, iStart, iEnd, duration, studyDescription);
    }

    public void addPatient(String patientID, String iStart, String iEnd, double duration, String studyDescription) {
        boolean merged = false;
        if (patientHashMap.containsKey(patientID)) {
            Patient patientObj = patientHashMap.get(patientID);
            boolean status = patientObj.updateIfTheSameExam(iStart, iEnd);
            if (status) {
                patientObj.setMerged();
                patientHashMap.put(patientID, patientObj);

                String tempID = patientID + "_";
                if (patientHashMap.get(tempID)!= null) {
                    Patient patientObj2 = patientHashMap.get(tempID);
                    String start2 = patientObj2.getStartTime();
                    String end2 = patientObj2.getEndTime();
                    boolean status2 = patientObj.updateIfTheSameExam(start2, end2);
                    if (status2) {
                        int studiesFrom2 = patientObj2.getNoOfStudiesInTheExam();
                        int studiesFrom1 = patientObj.getNoOfStudiesInTheExam();
                        patientObj.setNoOfStudiesInTheExam(studiesFrom1 + studiesFrom2);
                        patientHashMap.put(patientID, patientObj);
                        patientHashMap.remove(tempID);
                        String nextID = tempID + "_";
                        while (patientHashMap.containsKey(nextID)) {
                            Patient tempPatient = patientHashMap.get(nextID);
                            patientHashMap.put(tempID, tempPatient);
                            patientHashMap.remove(nextID);
                            tempID = nextID;
                            nextID = tempID + "_";
                        }
                    }
                }
            } else {
                addPatient(patientID + "_", iStart, iEnd, duration, studyDescription);
            }
        } else {
            Patient patientObj = new Patient(patientID, iStart, iEnd, duration, merged, studyDescription);
            patientHashMap.put(patientID, patientObj); // New Entry for the patient
        }
    }

    public Scanner(String scannerID, String patientID, String iStart, String iEnd, double duration, String studyDescription) {
        this.scannerID = scannerID;
        begin = iStart;
        end = iEnd;
        totalDuration = getDiffInMins(begin, end);
        addToPatientHashmap(patientID, iStart, iEnd, duration, studyDescription);
    }

    public String traversePatientHashMap() {
        StringBuilder out = new StringBuilder();
        out.append(scannerID + ", " + getUtilizedPercentage() + "\n");
        for (Patient patient: patientHashMap.values()) {
            out.append(patient.logThePatient());
        }
        return out.toString();
    }
}
