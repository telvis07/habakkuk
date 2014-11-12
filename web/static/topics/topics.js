/**
 * Created by telvis on 11/3/14.
 */
function TopicCtrl($window, $scope, $log){
    $scope.results = $window.HK.results;
}

var topicModule = angular.module("topicApp", []);
topicModule.controller("TopicCtrl", TopicCtrl);