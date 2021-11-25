import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatSnackBar, MatDialog } from '@angular/material';
import { GetDataService } from '../../../shared/services/get-data.service';
import { PopupadviceComponent } from './../../../shared/popup/popupadvice/popupadvice.component';

@Component({
  selector: 'app-partners',
  templateUrl: './partners.component.html',
  styleUrls: ['./partners.component.scss']
})
export class PartnersComponent implements OnInit {
  relativeType: boolean;
  agree: boolean;
  public username: string;
  public userphone: string;
  public useremail: string;
  public typesFeedback: any[];

  userDataForm = new FormGroup({
    fioControl: new FormControl('', [Validators.required, Validators.minLength(8), Validators.pattern(/\s/igm)]),
    phoneControl: new FormControl('', Validators.required)
  });

  constructor(
    private getDataService: GetDataService,
    private snackBar: MatSnackBar,
    private dialog: MatDialog
  ) { }

  ngOnInit() {
    this.relativeType = true;
    this.agree = true;
    // this.getDataService.getAdviceTypes().subscribe((data) => {
    //   this.typesFeedback = data;
    // });
  }

  sendMessage() {
    let type = this.typesFeedback.find(i => i.type_name == 'Заявка стать представителем').id;
    if (this.username && this.userphone && type) {
      let email = (this.useremail) ? this.useremail : 'info@dari-cosmetics.ru';
      this.getDataService.sendFeedback(this.username, this.userphone, 0, 'Заявка стать представителем (' + new Date() + ')', email , type).subscribe((res) => {
        if (res) {
          this.username = '';
          this.userphone = '';
          this.snackBar.open('Заявка отправлена', 'x', {
            duration: 3000
          });
        }
      });
    } else {
      this.snackBar.open('Все поля обязательны для заполнения', 'x', {
        duration: 3000
      });
    }
  }

  openPopup() {
    this.dialog.open(PopupadviceComponent, {
      data: {
        type: 'consult',
        partner: true
      }
    });
    // dialogRef.afterClosed().subscribe((res) => {
    //   if (res) {
    //     if (res.name && res.phone) {
    //       this.username = res.name;
    //       this.userphone = res.phone;
    //       this.useremail = res.email;
    //       this.sendMessage();
    //     }
    //   }
    // });
  }

  openDoc() {
    window.open('/assets/docs/personal_data.pdf', '_blank');
  }

}
