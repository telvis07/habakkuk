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
        window.HK.search_results = [];
    }));

    it('creates a BibleStudyCtrl controller', function(){
        var ctrl = controller('BibleStudyCtrl', {$window: window, $scope: scope});
        expect(ctrl).toBeDefined();
    });
});