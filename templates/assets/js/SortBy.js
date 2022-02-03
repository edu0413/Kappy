$(document).on("change", ".form-control", function() {
  var sortingMethod = $(this).val();
  
  if(sortingMethod == 'Preço Ascendente') {
    sortProductsPriceAscending();
  } else if (sortingMethod == 'Preço Descendente') {
    sortProductsPriceDescending();
  }
});

function sortProductsPriceAscending() {
  var gridItems = $('.grid-item');

  gridItems.sort(function(a, b) {
    return $('.product-card', a).data("price") - $('.product-card', b).data("price");
  });

  $(".isotope-grid").append(gridItems);
}

function sortProductsPriceDescending() {
  var gridItems = $('.grid-item');

  gridItems.sort(function(a, b) {
    return $('.product-card', b).data("price") - $('.product-card', a).data("price");
  });

  $(".isotope-grid").append(gridItems);
}