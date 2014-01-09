/**
 * Created by telvis on 12/30/13.
 */
var bibleStudyModule = angular.module("bibleStudyApp", ['ngGrid']);

function BibleStudyCtrl($window, $scope, $log){
    /* Controller for BibleStudy app */
    $scope.search_text = null;
    $scope.popular_list = {};
    $scope.popular_list_selected_item = null;
    $scope.habakkuk_message = null;
    $scope.search_results = {};
    $scope.show_habakkuk_message = true;
    $scope.pagination = {"start_enabled":"disabled",
                         "end_enabled":"disabled"}
    $scope.num_search_result_pages = _.range(1,2);

    // Testing...
    $scope.popular_list = $window.HK.popular_list;
    $scope.search_results = $window.HK.search_results;
    $scope.search_results_count = $scope.search_results.length;
    $scope.total_search_results_count = $scope.search_results.length;
    $scope.habakkuk_message = $window.HK.habakkuk_message;

    $scope.gridOptions = {
        data: 'popular_list',
        columnDefs: [{field:'term', displayName:'Bible Reference'},
                     {field: 'count', displayName: 'Popularity'}],
        enableSorting: true,
        multiSelect: false,
        sortInfo: { fields: ['count', 'term'], directions: ['desc','asc'] }
    };
}


bibleStudyModule.controller("BibleStudyCtrl", BibleStudyCtrl);