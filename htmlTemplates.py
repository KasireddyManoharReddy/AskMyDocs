css = """
<style>

#MainMenu{
visibility:hidden;
}

footer{
visibility:hidden;
}

header{
visibility:hidden;
}

.stApp{
background:#111827;
}

.chat-message{
display:flex;
padding:18px;
margin-bottom:15px;
border-radius:18px;
align-items:flex-start;
}

.chat-message.user{

background:#1f2937;

border:1px solid #374151;

box-shadow:0 2px 6px rgba(0,0,0,0.25);
}

.chat-message.bot{

background:#1e3a5f;

border:1px solid #2563eb;

box-shadow:0 2px 8px rgba(0,0,0,0.25);
}

.avatar{

flex:0 0 50px;

width:50px;

height:50px;

margin-right:15px;
}

.avatar img{

width:100%;

height:100%;

border-radius:50%;

object-fit:cover;
}

.message{

color:white;

font-size:16px;

line-height:1.7;
}

</style>
"""


user_template = """
<div class="chat-message user">

<div class="avatar">

<img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png">

</div>

<div class="message">

{{MSG}}

</div>

</div>
"""


bot_template = """
<div class="chat-message bot">

<div class="avatar">

<img src="https://cdn-icons-png.flaticon.com/512/4712/4712109.png">

</div>

<div class="message">

{{MSG}}

</div>

</div>
"""