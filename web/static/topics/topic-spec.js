/**
 * Created by telvis on 11/7/14.
 */
describe("Controller: TopicCtrl", function(){
    beforeEach(module('topicApp'));
    var scope, window, controller;

    beforeEach(inject(function($controller, $rootScope){
        // Mock Bootstrapped data from templates/topics/topic.html
        scope = $rootScope.$new();
        controller = $controller;
        window = {};
        window.HK = {'results':{}};
    }));

    it('creates a TopicCtl controller', function(){
        var ctrl = controller('TopicCtrl', {$window: window, $scope: scope});
        expect(ctrl).toBeDefined();
    });

    it('tests splitting the results list into 3 parts', function(){
        var ctrl = controller('TopicCtrl', {$window: window, $scope: scope});
        ret = ctrl.split_results_into_columns(undefined, 3);
        expect(ret).toEqual([[],[],[]]);

        ret = ctrl.split_results_into_columns(['one', 'two', 'three', 'four'], 3);
        expect(ret).toEqual([['one', 'four'],['two'],['three']]);
    });
});