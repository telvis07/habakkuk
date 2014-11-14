/**
 * Created by telvis on 11/3/14.
 */
function TopicCtrl($window, $scope, $log){

    var split_results_into_columns = function(result_list, num_columns)
    {


        /* Split topics results in to columns*/
        var split_results_list = [];
        var idx;

        for (i=0; i<num_columns; i++){
            split_results_list.push([]);
        };

        if (!result_list){
            return split_results_list;
        }

        for (i = 0; i < result_list.length; i++) {
            idx = i % num_columns;
            $log.info("[split_results_into_columns] adding item to "+idx);
            split_results_list[idx].push(result_list[i]);
        };
        return split_results_list;
    };

    $scope.results = $window.HK.results;
    $scope.result_columns = split_results_into_columns($scope.results.topics, 3);
};

var topicModule = angular.module("topicApp", []);
topicModule.controller("TopicCtrl", TopicCtrl);