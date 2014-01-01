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

    // Testing...
    $scope.popular_list = $window.HK.popular_list;
    $scope.search_results = $window.HK.search_results;
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