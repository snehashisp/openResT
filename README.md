## openResT
version 0.1

<br/><br/>
A Framework for REST based api testing with JSON schema based validation. 
Core functionalities (Implemented in current version)
<ol>
    <li> Creating tests in JSON </li>
    <li> Organizing tests into domains </li>
    <li> Running domains and tests within 
        <ol>
            <li> Running tests once synchronously </li>
            <li> Running tests multiple times (for stress testing API) asynchronously. </li>
		    <li> Running all tests in a domain asynchronously all at once. </li>
        </ol>
    <li> Checking for status errors </li>
    <li> Validating using JSON schema </li> 
    <li> Calulating response times </li>
    <li> Error logging in csv. </li>  
    <li> AWS SNS based error notifications. </li>
</ol>
<br/>
Considerations: At current implementation levels openResT is a framework providing the foundation for
the above functionalities and not a full fledged application or a library. The following sections will 
outline the structure and philosophy of the framework. Users can (should) extend the functionalities of 
the module to meet their demands. 

