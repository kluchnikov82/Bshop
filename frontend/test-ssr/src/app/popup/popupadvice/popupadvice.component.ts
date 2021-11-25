import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA, MatSnackBar } from '@angular/material';
import { GetDataService } from '../../services/get-data.service';
import { registerLocaleData, isPlatformBrowser } from '@angular/common';
import ru from '@angular/common/locales/ru';

@Component({
  selector: 'app-popupadvice',
  templateUrl: './popupadvice.component.html',
  styleUrls: ['./popupadvice.component.scss']
})
export class PopupadviceComponent implements OnInit {

  public adviceType: string;
  public subjectName: string;
  public rating: number[] = [1, 2, 3, 4, 5];
  public curRate = 0;
  public errorText: string;
  public showError: boolean;
  public adviceText: string;
  public adviceUrl: string;
  public username: string;
  public userphone: string;
  public useremail: string;
  subjectId: string;

  constructor(
    public dialogRef: MatDialogRef<PopupadviceComponent>,
    private getDataService: GetDataService,
    public snackBar: MatSnackBar,
    @Inject(MAT_DIALOG_DATA) public data: any,
    @Inject(PLATFORM_ID) private platformId: Object
  ) { }

  ngOnInit() {
    registerLocaleData( ru );
    if (this.data) {
      this.adviceType = this.data.type;
      this.subjectName = this.data.name;
      this.subjectId = this.data.id;
    }
  }

  closePopup(res: string = '') {
    this.dialogRef.close(res);
  }

  chooseRating(index: number) {
    this.curRate = index;
    this.showError = false;
  }

  checkBonusActive(bonus) {
    let res;
    if (bonus && bonus.amount > 0) {
      if (bonus.created) {
        const today = new Date();
        const bonusDate = new Date(bonus.created);
        const activateDate = new Date(bonusDate.setDate(bonusDate.getDate() + 14));
        if (today < activateDate) {
          res = activateDate;
        }
      }
    }
    return res;
  }

  send() {
    if (this.data.type === 'consult') {
      if (this.data.partner) {
        this.dialogRef.close({name: this.username, phone: this.userphone, email: this.useremail});
      } else {
        this.dialogRef.close({name: this.username, phone: this.userphone});
      }
     } else if (this.data.type === 'history') {
       this.showError = false;
       this.closePopup();
     } else {
      if (!this.curRate) {
        this.showError = true;
        this.errorText = 'Поставьте, пожалуйста, оценку ' + (this.adviceType === 'kit') ? 'программе' : 'товару';
        return;
      }
      if (!this.adviceText) {
        this.showError = true;
        this.errorText = 'Напишите, пожалуйста, пару слов о ' + (this.adviceType === 'kit') ? 'программе' : 'товаре';
        return;
      }
      this.showError = false;
      if (this.adviceType === 'kit') {
        this.getDataService.sendKitAdvice(this.subjectId, this.adviceText, this.adviceUrl).subscribe((res) => {
          if (res) {
            this.snackBar.open('Спасибо за Ваш отзыв!', 'x', {
              duration: 3000
            });
          }
        });
      } else {
        this.getDataService.sendProductAdvice(this.subjectId, this.adviceText, this.adviceUrl, this.curRate).subscribe((res) => {
          if (res) {
            this.snackBar.open('Спасибо за Ваш отзыв!', 'x', {
              duration: 3000
            });
          }
        });
      }
      this.closePopup();
    }
  }

  changePass() {
    if (this.data.type === 'forgot') {
      if (this.useremail) {
        this.getDataService.resetPassword(this.useremail.toLowerCase()).subscribe((res) => {
          if (res) {
            this.snackBar.open(res.message, 'x', {
              duration: 5000
            });
          }
        }, (err) => {
          this.snackBar.open(err.error.message, 'x', {
            duration: 5000
          });
        });
      }
      this.closePopup();
    }
  }

  getUserName(comment) {
    if (comment) {
      if (comment.user.last_name) {
        return comment.user.first_name + ' ' + comment.user.last_name;
      } else {
        return '';
      }
    } else {
      return '';
    }
  }

  openDoc() {
    if (isPlatformBrowser(this.platformId)) {
      window.open('https://dari-cosmetics.ru/assets/docs/personal_data.pdf', '_blank');
    }
  }

}
