package J1121_1;

import java.util.Scanner;

public class J1121_7 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		Scanner scn = new Scanner(System.in);
		int OnePrice = 200,Qty;
		double TotalPrice;
		        
		System.out.println("每張入場卷價格為" + OnePrice + "元");
		System.out.print("請輸入您要購買的張數:");        
		Qty = Integer.parseInt(scn.nextLine());
		System.out.println("==========================");
		TotalPrice = OnePrice * Qty;
		if(Qty>=10){
		   TotalPrice = OnePrice * Qty * 0.9;
		   System.out.println("購買10張以上打九折");
		}else{
		    TotalPrice = OnePrice * Qty;
		    System.out.println("您未購買10張以上的入場券,恕不打折");
		}
		System.out.println("總價為" + TotalPrice + "元");
		scn.close();
		
	}

}
