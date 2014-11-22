/**
 * Created by telvis on 11/3/14.
 */
function TopicCtrl($window, $scope, $log){
    this.split_results_into_columns = function(result_list, num_columns)
    {
        /* Split topics results in to `num_columns` columns*/
        $log.info("in split_results_into_columns")

        var split_results_list = [];
        var idx;

        for (i=0; i<num_columns; i++){
            split_results_list.push([]);
        };

        if (!result_list){
            /* case when result_list is empty */
            return split_results_list;
        }

        for (i = 0; i < result_list.length; i++) {
            idx = i % num_columns;
            split_results_list[idx].push(result_list[i]);
        };

        return split_results_list;
    };

    $scope.results = $window.HK.results;
    $scope.result_columns = this.split_results_into_columns($scope.results.topics, 3);
};



var topicModule = angular.module("topicApp", []);
topicModule.controller("TopicCtrl", TopicCtrl);