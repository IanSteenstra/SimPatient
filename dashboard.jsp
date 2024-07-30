<%@page import="java.util.Random"%>
<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Motivational Interviewing Evaluation Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body {
    font-family: sans-serif;
}

.chart-container {
    display: inline-block;
    width: 48%;
    margin: 1%;
}
</style>
</head>
<body>

<h1>Motivational Interviewing Evaluation Dashboard</h1>

<div class="chart-container">
    <h2>MI Global Scores</h2>
    <canvas id="miGlobalScoresChart"></canvas>
</div>

<div class="chart-container">
    <h2>Adherence to MI Principles</h2>
    <canvas id="miAdherenceChart"></canvas>
</div>

<div class="chart-container" style="width: 98%">
    <h2>Frequency of MI Behaviors</h2>
    <canvas id="miBehaviorsChart"></canvas>
</div>

<script>
// Generate random data for demonstration purposes
var randomValue = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

// MI Global Scores Chart
var ctxGlobalScores = document.getElementById('miGlobalScoresChart').getContext('2d');
var globalScoresData = {
    labels: ['Partnership', 'Empathy', 'Cultivating Change Talk', 'Softening Sustain Talk'],
    datasets: [{
        label: 'MI Global Scores',
        data: [randomValue(1, 4), randomValue(1, 4), randomValue(1, 4), randomValue(1, 4)],
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
    }]
};
var miGlobalScoresChart = new Chart(ctxGlobalScores, {
    type: 'radar',
    data: globalScoresData,
    options: {
        scale: {
            ticks: {
                beginAtZero: true,
                max: 4
            }
        }
    }
});

// MI Adherence Chart
var ctxAdherence = document.getElementById('miAdherenceChart').getContext('2d');
var adherenceData = {
    labels: ['MI Adherent', 'MI Non-Adherer'],
    datasets: [{
        data: [randomValue(60, 90), randomValue(10, 40)],
        backgroundColor: ['rgba(153, 255, 153, 1)', 'rgba(255, 102, 102, 1)'],
    }]
};
var miAdherenceChart = new Chart(ctxAdherence, {
    type: 'pie',
    data: adherenceData,
});

// MI Behaviors Chart
var ctxBehaviors = document.getElementById('miBehaviorsChart').getContext('2d');
var behaviorLabels = ['Gi', 'Persuade', 'Persuade with', 'Q', 'SR', 'CR', 'AF', 'Seek', 'Emphasize', 'Confront'];
var behaviorData = behaviorLabels.map(() => randomValue(1, 20));
var miBehaviorsChart = new Chart(ctxBehaviors, {
    type: 'bar',
    data: {
        labels: behaviorLabels,
        datasets: [{
            label: 'Frequency',
            data: behaviorData,
            backgroundColor: 'rgba(255, 153, 153, 0.8)',
            borderColor: 'rgba(255, 102, 102, 1)',
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});
</script>

</body>
</html>