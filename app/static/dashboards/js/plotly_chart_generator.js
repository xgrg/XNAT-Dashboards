
function chart_generator(json){
    var graph_name = "";
    var graph_info = {};
    for (var g_name in json){
        graph_name = g_name;
        graph_info = json[g_name];
    }
    barchart_generator(graph_name,graph_info)
}  

function getRandomIntInclusive(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function barchart_generator(graph_name, graph_info){
    x_axis = [];
    y_axis = [];
    for (x in graph_info){
        if(x == 'graph_type' || x == 'id'){
            continue;
        }else{
            x_axis.push(x);
            y_axis.push(graph_info[x]);
        }
    }
    r = getRandomIntInclusive(0,254);
    g = getRandomIntInclusive(0,254);
    b = getRandomIntInclusive(0,254);
    var data = [
        {
          x: x_axis,
          y: y_axis,
          type: 'bar',
          marker: {
            color: 'rgb('+r+','+g+','+b+')'
          }
        }
      ];

      var layout = {
        title: graph_name,
        showlegend: false
    };

    var config = {responsive: true}
    
    Plotly.newPlot('graph_body'+graph_info['id'], data, layout, config);

}
