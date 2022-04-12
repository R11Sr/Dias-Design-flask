/* Add your Application JavaScript */


// Add Item to cart with AJAX
window.addEventListener('load',(e)=>{


    $(".addToCartForm").on('submit',(event)=>{
        
        console.log(`event: ${event.target.id}`);
        $.ajax({
            data :{
                prod_id : `${event.target.id}`
            },
            type: 'POST',
            url: '/add-to-cart'
        }).done((response)=>{
            $('#cart-display').effect("shake");
            set_cart();
    
        }).fail(()=>{
            alert('An Error has occured please contact the Administrator');
        });
        event.preventDefault(); 
    })
});


    // Remove Items from Cart With AJAX
window.addEventListener('load',(e)=>{
    

    console.log( $(".RemoveItem"));

    $(".RemoveItem").on('submit',(event)=>{
        
        console.log(`event: ${event.target.id}`);
        $.ajax({
            data :{
                lineItem_id : `${event.target.id}`
            },
            type: 'POST',
            url: '/remove-from-cart'
        }).done((response)=>{
            console.log(response)
            $(".table-body").empty();
            $(".table-body").append(response);
            $('#cart-display').effect("shake");
            set_cart();
    
        }).fail(()=>{
            alert('An Error has occured please contact the Administrator');
        });
        event.preventDefault(); 
    })


});
   

function set_cart(){
    $.ajax({
        data :{
            user :$('#user_id').val()
        },
        type: 'POST',
        url: '/set-cart-amount'
    }).done((response)=>{
        $('#cart-amount').text(response.lineItems);

    });  
}
    



// Show current Items in cart upon loading

$(document).ready(()=>{
    $.ajax({
        data :{
            user :$('#user_id').val()
        },
        type: 'POST',
        url: '/set-cart-amount'
    }).done((response)=>{
        $('#cart-amount').text(response.lineItems);

    });

});


// make table rows clickable 
$(document).ready(()=>{
    $(".clickable-row").click(function() {
         window.location = $(this).data("href");
     });
})