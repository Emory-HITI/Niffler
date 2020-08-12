package edu.emory.bmi.niffler.csv.scanner_util;

import edu.emory.bmi.niffler.util.NifflerConstants;
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

    private Map<String, Patient> examsHashMap = new HashMap<>();
    private Map<String, Double> patientHashMap = new HashMap<>();
    private String scannerID;
    private String begin;
    private String end;
    private double totalDuration;
    private String modality;
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
        Collection<Patient> patients = examsHashMap.values();
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

        double cumulativeDuration = duration;
        if (patientHashMap.get(patientID)!=null) {
            cumulativeDuration += patientHashMap.get(patientID);
        }
        patientHashMap.put(patientID, cumulativeDuration);
        addPatient(patientID, iStart, iEnd, duration, studyDescription);
    }

    public void addPatient(String patientID, String iStart, String iEnd, double duration, String studyDescription) {
        boolean merged = false;
        if (examsHashMap.containsKey(patientID)) {
            Patient patientObj = examsHashMap.get(patientID);
            boolean status = patientObj.updateIfTheSameExam(iStart, iEnd);
            if (status) {
                patientObj.setMerged();
                String temp = patientObj.getStudyDescription();
                patientObj.setStudyDescription(temp + NifflerConstants.STUDY_DESC_SEPARATOR + studyDescription);
                examsHashMap.put(patientID, patientObj);

                String tempID = patientID + NifflerConstants.PATIENT_DIFFERENTIATOR;
                if (examsHashMap.get(tempID)!= null) {
                    Patient patientObj2 = examsHashMap.get(tempID);
                    String start2 = patientObj2.getStartTime();
                    String end2 = patientObj2.getEndTime();
                    boolean status2 = patientObj.updateIfTheSameExam(start2, end2);
                    if (status2) {
                        int studiesFrom2 = patientObj2.getNoOfStudiesInTheExam();
                        int studiesFrom1 = patientObj.getNoOfStudiesInTheExam();
                        String descFrom2 = patientObj2.getStudyDescription();
                        String descFrom1 = patientObj.getStudyDescription();
                        patientObj.setNoOfStudiesInTheExam(studiesFrom1 + studiesFrom2);
                        patientObj.setStudyDescription(descFrom1 + NifflerConstants.STUDY_DESC_SEPARATOR + descFrom2);
                        examsHashMap.put(patientID, patientObj);
                        examsHashMap.remove(tempID);
                        String nextID = tempID + NifflerConstants.PATIENT_DIFFERENTIATOR;
                        while (examsHashMap.containsKey(nextID)) {
                            Patient tempPatient = examsHashMap.get(nextID);
                            examsHashMap.put(tempID, tempPatient);
                            examsHashMap.remove(nextID);
                            tempID = nextID;
                            nextID = tempID + NifflerConstants.PATIENT_DIFFERENTIATOR;
                        }
                    }
                }
            } else {
                addPatient(patientID + NifflerConstants.PATIENT_DIFFERENTIATOR, iStart, iEnd, duration, studyDescription);
            }
        } else {
            Patient patientObj = new Patient(patientID, iStart, iEnd, duration, merged, studyDescription);
            examsHashMap.put(patientID, patientObj); // New Entry for the patient
        }
    }

    public Scanner(String scannerID, String patientID, String iStart, String iEnd, double duration,
                   String studyDescription, String modality) {
        this.scannerID = scannerID;
        this.modality = modality;
        begin = iStart;
        end = iEnd;
        totalDuration = getDiffInMins(begin, end);
        addToPatientHashmap(patientID, iStart, iEnd, duration, studyDescription);
    }

    public String traversePatientHashMap(int index, String date) {
        StringBuilder out = new StringBuilder();

        int noOfStudies = 0;
        for (Patient patient: examsHashMap.values()) {
            noOfStudies += patient.getNoOfStudiesInTheExam();
        }

        out.append(index + ", " + date + ", " + scannerID + ", " + getUtilizedPercentage() + ", " +
                patientHashMap.size() + ", " + examsHashMap.size() + ", " + noOfStudies + "," + modality + "\n");
        for (Patient patient: examsHashMap.values()) {
            out.append(patient.logThePatient());
        }
        return out.toString();
    }
}
