/* Add your Application JavaScript */


// Add Item to cart with AJAX

window.addEventListener('load',(e)=>{

    console.log( $(".addToCartForm"));

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
            $('#cart-amount').text(response.cart);
    
        }).fail(()=>{
            alert('Ajax failed');
        });
        event.preventDefault(); 
    })
    });




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