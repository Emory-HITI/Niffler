package edu.emory.bmi.niffler.csv.scanner_util;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;


import static edu.emory.bmi.niffler.csv.scanner_util.ScannerUtil.getDiffInMins;

/**
 * Represents a patient.
 */
public class Patient {
    private static Logger logger = LogManager.getLogger(Patient.class.getName());

    private String startTime;
    private String endTime;
    private String patientID;
    private double duration;
    private String studyDescription;

    private int noOfStudiesInTheExam = 1;
    private int noOfSeriesInTheExam;

    public Patient(String patientID, String startTime, String endTime, double duration, boolean merged,
                   String studyDescription, int noOfSeries) {
        this.patientID = patientID;
        this.startTime = startTime;
        this.endTime = endTime;
        this.duration = duration;
        if (merged) {
            noOfStudiesInTheExam += 1;
        }
        noOfSeriesInTheExam = noOfSeries;
        this.studyDescription = studyDescription;
    }

    public String getStartTime() {
        return startTime;
    }

    public String getEndTime() {
        return endTime;
    }

    public void setMerged() {
        noOfStudiesInTheExam += 1;
    }


    public int getNoOfStudiesInTheExam() {
        return noOfStudiesInTheExam;
    }

    public int getNoOfSeriesInTheExam() {
        return noOfSeriesInTheExam;
    }

    public void setNoOfSeriesInTheExam(int noOfSeriesInTheExam) {
        this.noOfSeriesInTheExam = noOfSeriesInTheExam;
    }

    public void setNoOfStudiesInTheExam(int noOfStudiesInTheExam) {
        this.noOfStudiesInTheExam = noOfStudiesInTheExam;
    }

    public void setStudyDescription(String studyDescription) {
        this.studyDescription = studyDescription;
    }

    public String getStudyDescription() {
        return studyDescription;
    }

    public double getDurationInMins() {
        double durationInMins = getDiffInMins(startTime, endTime);
        duration = durationInMins;
        return durationInMins;
    }


    public boolean updateIfTheSameExam (String newStart, String newEnd) {

        // TODO: Consider for 2359 -> 0000 cases.
        double s1e1 = getDiffInMins(startTime, endTime);
        double s2e2 = getDiffInMins(newStart, newEnd);

        // Check for same or multiple exams.
        double s1s2 = getDiffInMins(startTime, newStart);
        double e1e2 = getDiffInMins(endTime, newEnd);
        double e1s2 = getDiffInMins(endTime, newStart);
        double e2s1 = getDiffInMins(newEnd, startTime);
        if (s1s2 >= 0 && e1e2 < 0) {
            logger.debug("case 1: " + patientID + ", " + s1s2 + ", " + e1e2);
            // same exam. no change. s2e2 inside s1e1.
            return true;
        } else if (s1s2 >= 0 && e1e2 >= 0) {
            if (e1s2 < 20) {
                logger.debug("case 2: " + patientID + ", " + s1s2 + ", " + e1e2);
                // same exam. s the same. e changes.
                endTime = newEnd;
                return true;
            } else {
                logger.debug("case 3: " + patientID + ", " + s1s2 + ", " + e1e2);
                // different exam
                return false;
            }
        } else if (s1s2 < 0 && e1e2 < 0) {
            if (e2s1 < 20) {
                logger.debug("case 4: " + patientID + ", " + s1s2 + ", " + e1e2);
                // same exam. s changes. e the same.
                startTime = newStart;
                return true;
            } else {
                logger.debug("case 5: " + patientID + ", " + s1s2 + ", " + e1e2);
                // different exam
                return false;
            }
        } else if (s1s2 < 0 && e1e2 >= 0) {
            logger.debug("case 6: " + patientID + ", " + s1s2 + ", " + e1e2);
            // same exam. both changes. s1e1 inside s2e2.
            startTime = newStart;
            endTime = newEnd;
            return true;
        } else {
            logger.debug("Case that was not captured");
        }
        return false;
    }

    public String logThePatient() {
        getDurationInMins();
        return ", , , , , , , , ," + patientID + ", " + startTime + ", " + endTime + ", " + duration + ", " +
                noOfStudiesInTheExam + ", " + noOfSeriesInTheExam + ", " + studyDescription + "\n";
    }
}
