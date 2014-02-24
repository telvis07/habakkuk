/**
 * Created by telvis on 1/8/14.
 */
describe("Controller: BibleStudyCtrl", function() {
    beforeEach(module('bibleStudyApp'));
    var scope, window, controller;

    beforeEach(inject(function($controller, $rootScope){
        scope = $rootScope.$new();
        controller = $controller;
        window = {};
        window.HK = {};
        window.HK.popular_list = [];
        window.HK.search_results = {};
        window.HK.search_results.results = [];
        window.HK.search_results.habakkuk_message = "testing";
    }));

    it('creates a BibleStudyCtrl controller', function(){
        var ctrl = controller('BibleStudyCtrl', {$window: window, $scope: scope});
        expect(ctrl).toBeDefined();
    });

    it('verifies default scope values', function(){
        var ctrl = controller('BibleStudyCtrl', {$window: window, $scope: scope});
        expect(scope.popular_list).toEqual([]);
        expect(scope.search_results.results).toEqual([]);
        expect(scope.search_results.count).toEqual(0, "search_results.count is wrong");
        expect(scope.search_results.total).toEqual(0, "search_results.total is wrong");
        expect(scope.search_results.habakkuk_message).toEqual("testing");
        expect(scope.gridOptions).toBeDefined();
        expect(scope.text_search).toBeDefined();
        expect(scope.popular_list_selected_item).toBeDefined();
        expect(scope.show_habakkuk_message).toBe(true);
        expect(scope.pagination).toEqual({"start_enabled":"disabled",
                         "end_enabled":"disabled"});
        expect(scope.num_search_result_pages).toEqual(_.range(1,2));
    });
});