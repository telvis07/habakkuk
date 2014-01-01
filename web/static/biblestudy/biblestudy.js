/**
 * Created by telvis on 12/30/13.
 */

function BibleStudyCtrl($window, $scope, $log){
    /* Controller for BibleStudy app */
    $scope.search_text = null;
    $scope.popular_list = {};
    $scope.popular_list_selected_item = null;
    $scope.habakkuk_message = null;
    $scope.search_results = {};
    $scope.show_habakkuk_message = true;

    // Testing...
    $scope.popular_list = $window.HK.popular_list;
    $scope.search_results = $window.HK.search_results;
    $scope.search_results_count = $scope.search_results.length;
    $scope.total_search_results_count = $scope.search_results.length;
    $scope.habakkuk_message = $window.HK.habakkuk_message;
    $scope.num_pages = 1;
    $scope.gridOptions = {
        data: 'popular_list',
        columnDefs: [{field:'term', displayName:'Bible Reference'},
                     {field: 'count', displayName: 'Popularity'}],
        enableSorting: true,
        multiSelect: false,
        sortInfo: { fields: ['count', 'term'], directions: ['desc','asc'] }
    };
}

var bibleStudyModule = angular.module("bibleStudyApp", ['ngGrid']);
bibleStudyModule.controller("BibleStudyCtrl", BibleStudyCtrl);