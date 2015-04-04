<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<?php
require_once ("config.php");
require_once ("parser.php");
$db_link = mysqli_connect ($dbhost, $dbuser, $dbpassword, $database);
?>


<html>
<head>
<title>BOSWatch</title>
<link rel="stylesheet" type="text/css" href="tooltip.css">
</head>
<body>

	<div style="text-align: center; width: 1250px; margin: 0px auto;">

		<h1>BOSWatch</h1>
		
		Last alarms for FMS and ZVEI (max. 50)<br><br>
		
		<div style="float: left; width: 800px;">
			<b>Last FMS alarms</b>
			<?php 
			$sql = "SELECT id, time, service, country, location, vehicle, status, direction, tsi FROM ".$tableFMS." ORDER BY id DESC LIMIT 50";
			$db_erg = mysqli_query( $db_link, $sql );
			 
			 
			echo '<table border="1" style="width: 800px;">';
			while ($data = mysqli_fetch_array( $db_erg, MYSQL_ASSOC))
			{
				$fms_id = $data['service'].$data['country'].$data['location'].$data['vehicle'].$data['status'].$data['direction'];
			  echo "<tr>";
				  echo "<td>". $data['id'] . "</td>";
				  echo "<td>". $data['time'] . "</td>";
				  echo "<td>". parse("service",$fms_id) . "</td>";
				  echo "<td>". parse("country",$fms_id) . "</td>";
				  echo "<td>". $data['location'] . "</td>";
				  echo "<td>". $data['vehicle'] . "</td>";
				  echo "<td>". $data['status'] . "</td>";
				  echo "<td>". parse("direction",$fms_id) . "</td>";
				  echo "<td>". $data['tsi'] . "</td>";
			  echo "</tr>";
			}
			echo "</table>";
			?>
		</div>
		
		<div style="float: right; width: 400px;">
			<b>Last ZVEI alarms</b>
			<?php 
			$sql = "SELECT id, time, zvei FROM ".$tableZVEI." ORDER BY id DESC LIMIT 50";
			$db_erg = mysqli_query( $db_link, $sql );
			 
			 
			echo '<table border="1" style="width: 400px;">';
			while ($data = mysqli_fetch_array( $db_erg, MYSQL_ASSOC))
			{
			  echo "<tr>";
				  echo "<td>". $data['id'] . "</td>";
				  echo "<td>". $data['time'] . "</td>";
				  echo "<td>". $data['zvei'] . "</td>";
			  echo "</tr>";
			}
			echo "</table>";
			?>
		</div>
		
	</div>

</body>
</html>