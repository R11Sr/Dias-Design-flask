/* Add your Application JavaScript */

window.addEventListener('load',(e)=>{

    $("#addToCartForm").on('submit',(event)=>{
        
        console.log(`product id: ${$('#prod_id').val()}`);
        $.ajax({
            data :{
                prod_id :$('#prod_id').val()
            },
            type: 'POST',
            url: '/add-to-cart'
            // url: '{{url_for("customer.add_to_cart")|tojson|safe}'
        }).done((response)=>{
            console.log(response);
            $('#cart-display').effect("shake");
            $('#cart-amount').text(response.cart);
    
        }).fail(()=>{
            alert('Ajax failed');
        });
        event.preventDefault(); 
    })
    });