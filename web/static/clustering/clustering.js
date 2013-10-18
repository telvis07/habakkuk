// angular app to browse habakkuk clusters and facet results

var clusterModule = angular.module("clusterApp",[]);

clusterModule.controller('ClusterCtrl',
   function ($scope, $log, clusterData){
     // clusters for queries
     $scope.clusters = clusterData.query(null);

     // TODO: move to service
     var get_facets = function(){
         return [
            {value:'john 3:16', count:'10', selected: false},
            {value:'genesis 2:24', count:'8', selected: false},
         ];
     };

     $scope.selectFacet = function(index){
         // update row color for selection
         var selected = !$scope.facets[index].selected;
         var bv = null;
         var selected_list = [];
         $scope.facets[index].selected = selected;
         if (selected){
           $log.info("selected "+index+" from facets table");
           $scope.facets[index].class = "success";
           bv = $scope.facets[index].value;
           // TODO: support multiple selections
         }else {
           $log.info("de-selected "+index+" from facets table");
           $scope.facets[index].class = "";
         }
          for (var i=0; i<$scope.facets.length; i++){
            var facet = $scope.facets[i];
            if (facet.selected===true){
              selected_list.push($scope.facets[i].value);
            }
         }
         // $scope.clusters = clusterData.query(bv);
         $scope.clusters = clusterData.query(bv);
    };

     $scope.facets = get_facets();
     console.log($scope.facets);
});

// service for clustering data
clusterModule.factory('clusterData', function() {
    // creating an object of type 'clusterData'
    var clusters = {};
    clusters.query = function(filter_bibleverse) {
        // TODO: query from django
        data =  {
          "name": "root", 
          "children": [
            {
              "size": 2, 
              "name": "john 3:16", 
              "bibleverses":[{verse:'john 3:16', weight:1.0},
                             {verse:'galatians 1:1', weight:0.001}],
              "children": [
                {
                  "name": "user1 ", 
                  "children": []
                }, 
                {
                  "name": "user2", 
                  "children": []
                }, 
              ]
            },
            {
              "size": 2, 
              "name": "genesis 2:24", 
              "bibleverses":[{verse:'genesis 2:24', weight:1.0},
                             {verse:'habakkuk 1:1', weight:0.001}],
              "children": [
                {
                  "name": "user3 ", 
                  "children": []
                }, 
                {
                  "name": "user4", 
                  "children": []
                }, 
              ]      
            },
          ]
        };

        // filter
        if (filter_bibleverse === null){
            return data;
        }else{
            // TODO: iterate of selected_list and filter based on multiple-selections
            var _filtered = {name:"root", children:[]};
            for (var i=0; i<data.children.length; i++){
                var cluster = data.children[i];
                for (var j=0; j<cluster.bibleverses.length; j++){
                    var bv = cluster.bibleverses[j].verse;
                    if (bv == filter_bibleverse){
                        _filtered.children.push(cluster);
                        break;
                    }
                }
            }
            return _filtered;
        }
    };
    return clusters;
});


clusterModule.directive('hkukClustersViz', function($log, $window) {
    var width = $(window).width() * 0.66;
         height = $(window).height();
    
      return {
        restrict: 'E',
        scope: {clusters:"="},
        link: function(scope, element, attrs){
           var cluster = d3.layout.cluster()
                .size([height, width - 160]);

           var diagonal = d3.svg.diagonal()
                .projection(function(d) { return [d.y, d.x]; });

           var svg = d3.select(element[0])
              .append("svg")
                .attr("width", width)
                .attr("height", height)
              .append("g")
                .attr("transform", "translate(40, 0)");

            scope.$watch('clusters', function(newVal, oldVal){
              if (newVal){
                $log.info("in watch "+newVal);
                $log.info(newVal);

                // remove so we can redraw
                svg.selectAll('*').remove();

                // convert json to array of nodes
                var nodes = cluster.nodes(newVal);
                // array of links from parent to child
                var links = cluster.links(nodes);

                // add the links
                _link = svg.selectAll(".link")
                    .data(links)
                    .enter()
                    .append("path")
                      .attr("class", "link")
                      .attr("d", diagonal);

                // add the nodes
                var node = svg.selectAll(".node")
                  .data(nodes)
                .enter().append("g")
                  .attr("class", "node")
                  .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });

                // add circle per node
                node.append("circle")
                  .attr("r", 4.5);

                // add text per node
                node.append("text")
                  .attr("dx", function(d) { return d.children ? -8 : 8; })
                  .attr("dy", 3)
                  .attr("text-anchor", function(d) { return d.children ? "end" : "start"; })
                  .text(function(d) { return d.name; });
              } // if (data)
            }); // watch
        }
    };
});
