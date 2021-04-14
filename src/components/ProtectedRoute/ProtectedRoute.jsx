import React,{useContext} from 'react'
import {Route, Redirect} from 'react-router-dom'
import UserContext from '../../context/UserContext';

function ProtectedRoute({componet:Component , ...rest}) {
  const {userData, setUserData } = useContext(UserContext);
  
  console.log(userData);

  if(userData.auth){
    console.log("userData");
    return ( <Route {...rest} render={(props) => (<Component {...props}/>)}/>)
  } else {
    
    return <Redirect to='/login'/> 
  }
 
}

export default ProtectedRoute
